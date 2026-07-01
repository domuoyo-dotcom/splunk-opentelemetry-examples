import express from 'express';
import bodyParser from 'body-parser';
import cors from 'cors';
import { ApolloServer } from '@apollo/server';
import { expressMiddleware } from '@as-integrations/express4';
import { trace } from '@opentelemetry/api';
import { typeDefs, resolvers } from './schema.js';
import { serverTimingPlugin } from './serverTimingPlugin.js';

const tracer = trace.getTracer('books-graphql-service');
const FRONTEND_ORIGIN = 'http://localhost:5173';

export async function createApp() {
    const apolloServer = new ApolloServer({
        typeDefs,
        resolvers,
        plugins: [serverTimingPlugin],
    });

    await apolloServer.start();

    const app = express();

    app.use(
        '/graphql',
        cors({
            origin: FRONTEND_ORIGIN,
            credentials: true,
        }),
        bodyParser.json(),
        expressMiddleware(apolloServer, {
            context: async ({ req, res }) => {
                const requestSpan = tracer.startSpan('graphql.request', {
                    attributes: {
                        'http.method': req.method,
                        'http.url': req.url,
                    },
                });

                return { req, res, otelSpan: requestSpan };
            },
        })
    );

    app.options(
        '/graphql',
        cors({
            origin: FRONTEND_ORIGIN,
            credentials: true,
        })
    );

    return { app, apolloServer };
}
