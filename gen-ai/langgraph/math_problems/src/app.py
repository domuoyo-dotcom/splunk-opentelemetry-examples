from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from typing import List, Any, Optional, Dict
from pydantic import BaseModel, Field
import uuid
import asyncio
from datetime import datetime
import time
from opentelemetry import trace
from langgraph.prebuilt import create_react_agent as _create_react_agent

tracer = trace.get_tracer("langgraph-example")

class State(TypedDict):
    messages: Annotated[List[Any], add_messages]
    question: str
    solution: str
    grade: str
    rationale: str

class MathQuestion(BaseModel):
    mathematics_branch: str = Field(description="Which branch of mathematics the question is part of.")
    rationale: str = Field(description="Why you chose this question and what you hope students will learn from it.")
    question: str = Field(description="The math question")

class AssignmentSolution(BaseModel):
    solution: str = Field(description="The solution to the math problem provided by the student.")

class AssignmentResult(BaseModel):
    grade: str = Field(description="The grade you've given to the student assignment.")
    rationale: str = Field(description="An explanation of why you gave the grade that you did.")

class MathProblems:
    def __init__(self):
        self.teacher_agent= None
        self.teacher_llm_with_output = None
        self.student_agent = None
        self.student_llm_with_output = None
        self.teaching_assistant_agent = None
        self.teaching_assistant_llm_with_output = None
        self.graph = None

    async def _create_llm(self, agent_name: str, *, temperature: float, session_id: str) -> ChatOpenAI:
        """Create an LLM instance decorated with tags/metadata for tracing."""
        model = "gpt-4o-mini"
        tags = [f"agent:{agent_name}", "langgraph-example"]
        metadata = {
            "agent_name": agent_name,
            "agent_type": agent_name,
            "session_id": session_id,
            "thread_id": session_id,
            "ls_model_name": model,
            "ls_temperature": temperature,
        }

        base = ChatOpenAI(
            model=model,
            temperature=temperature,
            tags=tags,
            metadata=metadata,
        )

        return base

    async def setup(self):

        teacher_llm = await self._create_llm(agent_name="teacher_agent", temperature=0.7, session_id=None)
        self.teacher_agent = _create_react_agent(teacher_llm, tools=[]).with_config(
            {
                "run_name": "teacher_agent",
                "tags": ["agent", "agent:teacher_agent"],
                "metadata": {"agent_name": "teacher_agent"},
            }
        )

        self.teacher_llm_with_output = teacher_llm.with_structured_output(MathQuestion)

        student_llm = await self._create_llm(agent_name="student_agent", temperature=0.7, session_id=None)
        self.student_agent = _create_react_agent(student_llm, tools=[]).with_config(
            {
                "run_name": "student_agent",
                "tags": ["agent", "agent:student_agent"],
                "metadata": {"agent_name": "student_agent"},
            }
        )
        self.student_llm_with_output = student_llm.with_structured_output(AssignmentSolution)

        teaching_assistant_llm = await self._create_llm(agent_name="teaching_assistant_agent", temperature=0.7, session_id=None)
        self.teaching_assistant_agent = _create_react_agent(teaching_assistant_llm, tools=[]).with_config(
            {
                "run_name": "teaching_assistant_agent",
                "tags": ["agent", "agent:teaching_assistant_agent"],
                "metadata": {"agent_name": "teaching_assistant_agent"},
            }
        )
        self.teaching_assistant_llm_with_output = teaching_assistant_llm.with_structured_output(AssignmentResult)

        await self.build_graph()

    async def teacher(self, state: State) -> Dict[str, Any]:

        INSTRUCTIONS = f"""
            You're a seasoned teacher with a knack for keeping students
            engaged with interesting and compelling math problems.
            "Your task is to create a question suitable for Grade 8 math students.
            "You should first choose which branch of mathematics the question will be part of.
            "Then provide a rationale for the question and what you hope students will learn from it.
            "The question itself should be in markdown format."""

        # Add in the system message
        found_system_message = False
        messages = state["messages"]
        for message in messages:
            if isinstance(message, SystemMessage):
                message.content = INSTRUCTIONS
                found_system_message = True

        if not found_system_message:
            messages = [SystemMessage(content=INSTRUCTIONS)] + messages

        # Run the ReAct agent
        agent_out = await self.teacher_agent.ainvoke(state)

        # agent_out typically includes "messages"
        messages = agent_out["messages"]
        last = messages[-1]
        if not isinstance(last, AIMessage):
            # If tools are used, you may need to locate the last AI message
            last = next(m for m in reversed(messages) if isinstance(m, AIMessage))

        # Cast final text into your schema
        result: AssignmentSolution = await self.teacher_llm_with_output.ainvoke(last.content)

        # Return typed output (and optionally keep messages updated)
        new_state = {
            "messages": [{"role": "assistant", "content": f"The question is: {result.question}"}],
            "question": result.question
        }

        return new_state

    async def student(self, state: State) -> Dict[str, Any]:

        INSTRUCTIONS = f"""You're a meticulous Grade 8 student with a keen eye for detail. You're known for
            your ability to apply logic to just about any math problem the teacher
            gives you.  Yet sometimes, you make things too darn complicated.
            Your task is to review the assigned math question and prepare a solution.
            The answer should be in markdown format and should show the steps you used to find the solution.
            Pass the final solution to the 'Teaching Assistant' agent."""

        # Add in the system message
        found_system_message = False
        messages = state["messages"]
        for message in messages:
            if isinstance(message, SystemMessage):
                message.content = INSTRUCTIONS
                found_system_message = True

        if not found_system_message:
            messages = [SystemMessage(content=INSTRUCTIONS)] + messages

        # Run the ReAct agent
        agent_out = await self.student_agent.ainvoke(state)

        # agent_out typically includes "messages"
        messages = agent_out["messages"]
        last = messages[-1]
        if not isinstance(last, AIMessage):
            # If tools are used, you may need to locate the last AI message
            last = next(m for m in reversed(messages) if isinstance(m, AIMessage))

        # Cast final text into your schema
        result: MathQuestion = await self.student_llm_with_output.ainvoke(last.content)

        # Return typed output (and optionally keep messages updated)
        new_state = {
            "messages": [{"role": "assistant", "content": f"The solution is: {result.solution}"}],
            "solution": result.solution,
        }

        return new_state

    async def teaching_assistant(self, state: State) -> Dict[str, Any]:

        INSTRUCTIONS = f"""
            You've been a teaching assistant for more than 10 years. When it comes
            to grading student assignments, you're tough, but fair.  You usually provide
            witty comments when grading an assignment.
            Your task is to review the assigned math question and the solution provided by the student.
            Grade the assignment and provide a rationale for the grade.
            The rationale should be in markdown format."""

        # Add in the system message
        found_system_message = False
        messages = state["messages"]
        for message in messages:
            if isinstance(message, SystemMessage):
                message.content = INSTRUCTIONS
                found_system_message = True

        if not found_system_message:
            messages = [SystemMessage(content=INSTRUCTIONS)] + messages

        # Run the ReAct agent
        agent_out = await self.teaching_assistant_agent.ainvoke(state)

        # agent_out typically includes "messages"
        messages = agent_out["messages"]
        last = messages[-1]
        if not isinstance(last, AIMessage):
            # If tools are used, you may need to locate the last AI message
            last = next(m for m in reversed(messages) if isinstance(m, AIMessage))

        # Cast final text into your schema
        result: AssignmentResult = await self.teaching_assistant_llm_with_output.ainvoke(last.content)

        # Return typed output (and optionally keep messages updated)
        new_state = {
            "messages": [{"role": "assistant", "content": f"The grade is: {result.grade}"}],
            "grade": result.grade,
            "rationale": result.rationale,
        }

        return new_state

    async def build_graph(self):
        # Set up Graph Builder with State
        graph_builder = StateGraph(State)

        # Add nodes
        graph_builder.add_node("teacher", self.teacher)
        graph_builder.add_node("student", self.student)
        graph_builder.add_node("teaching_assistant", self.teaching_assistant)

        # Add edges
        graph_builder.add_edge(START, "teacher")
        graph_builder.add_edge("teacher", "student")
        graph_builder.add_edge("student", "teaching_assistant")
        graph_builder.add_edge("teaching_assistant", END)

        # Compile the graph
        self.graph = graph_builder.compile()

    async def run(self, message):
        state = {
            "messages": message
        }

        with tracer.start_as_current_span("langgraph-example") as current_span:
            result = await self.graph.ainvoke(state)
            print(result["question"])
            print(result["solution"])
            print(result["grade"])
            print(result["rationale"])

def main():
   math_problems = MathProblems()
   asyncio.run(math_problems.setup())
   message = "Create a math question for a grade 8 student"
   asyncio.run(math_problems.run(message))
   # wait for evaluations before
   time.sleep(300)

if __name__ == "__main__":
    main()
