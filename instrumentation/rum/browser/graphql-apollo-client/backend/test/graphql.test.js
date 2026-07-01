import test from 'node:test';
import assert from 'node:assert/strict';
import { ApolloServer } from '@apollo/server';
import { typeDefs, resolvers } from '../schema.js';

test('GetBooks query returns book titles and authors', async () => {
    const server = new ApolloServer({ typeDefs, resolvers });

    await server.start();

    const response = await server.executeOperation({
        query: `
            query GetBooks {
                books {
                    title
                    author
                }
            }
        `,
    });

    await server.stop();

    assert.equal(response.body.kind, 'single');
    assert.deepEqual(structuredClone(response.body.singleResult.data?.books), [
        { title: 'The Awakening', author: 'Kate Chopin' },
        { title: 'City of Glass', author: 'Paul Auster' },
    ]);
});
