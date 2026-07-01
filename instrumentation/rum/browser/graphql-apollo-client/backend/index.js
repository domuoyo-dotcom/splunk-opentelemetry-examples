import http from 'http';
import { createApp } from './createApp.js';

const port = 4000;

async function start() {
    const { app } = await createApp();
    const httpServer = http.createServer(app);

    httpServer.listen(port, () => {
        console.log(`🚀 Server listening at http://localhost:${port}/graphql`);
    });
}

start().catch((err) => {
    console.error('Failed to start server', err);
    process.exit(1);
});
