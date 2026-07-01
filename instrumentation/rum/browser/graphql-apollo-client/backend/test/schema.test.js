import test from 'node:test';
import assert from 'node:assert/strict';
import { books, resolvers } from '../schema.js';

test('books resolver returns the seed catalog', () => {
    assert.deepEqual(resolvers.Query.books(), books);
    assert.equal(books.length, 2);
    assert.equal(books[0].title, 'The Awakening');
});
