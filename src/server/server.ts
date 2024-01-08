// import { WebSocket } from "ws";

import { z } from "zod";
import WebSocket, { WebSocketServer } from "ws";
// import { ServerMessageSchema } from "./serverTypes";

export const ServerMessageSchema = z.object({
  sender: z.string(),
  message: z.string(),
});

// const wss = new WebSocket.Server({ port: 8080 });

const wss = new WebSocketServer({ port: 8081 });
const address = wss.address();
console.log(`Serving at:`);
console.log(address);

wss.on("connection", (ws: WebSocket) => {
  console.log("New client connected");

  ws.on("message", (message: string) => {
    const msg = ServerMessageSchema.parse(JSON.parse(message));
    console.log(`Received message from ${msg.sender}: ${msg.message}`);
    // Process message here
  });

  ws.on("error", (err) => {
    console.error(err);
  });

  ws.on("close", () => {
    console.log("Client disconnected");
  });
});
