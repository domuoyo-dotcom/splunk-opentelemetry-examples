export const typeDefs = `#graphql
  type Book {
    title: String
    author: String
  }

  type Query {
    books: [Book]
  }
`;

export const books = [
    { title: 'The Awakening', author: 'Kate Chopin' },
    { title: 'City of Glass', author: 'Paul Auster' },
];

export const resolvers = {
    Query: {
        books: () => books,
    },
};
