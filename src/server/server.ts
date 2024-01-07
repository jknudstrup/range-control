// import { WebSocket } from "ws";
import WebSocket, { WebSocketServer } from "ws";

// const wss = new WebSocket.Server({ port: 8080 });

const wss = new WebSocketServer({ port: 8080 });

wss.on("connection", (ws: WebSocket) => {
  console.log("New client connected");

  ws.on("message", (message: string) => {
    console.log(`Received message: ${message}`);
    // Process message here
  });

  ws.on("close", () => {
    console.log("Client disconnected");
  });
});