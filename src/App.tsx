import { useEffect, useRef } from "react";
// import { WebSocket } from "ws";
import { ServerMessage } from "./server/serverTypes";
const PORT = 8081;

export const App = () => {
  const socketRef = useRef<WebSocket | null>(null);

  const sendToServer = (message: string) => {
    const serverMessage: ServerMessage = {
      sender: "range-control",
      message,
    };
    socketRef.current?.send(JSON.stringify(serverMessage));
  };

  useEffect(() => {
    socketRef.current = new WebSocket(`ws://localhost:${PORT}`);

    socketRef.current?.addEventListener("open", function (event) {
      sendToServer("hello server!!!");
    });

    socketRef.current?.addEventListener("message", function (event) {
      console.log("Message from server: ", event.data);
    });

    return () => {
      socketRef.current?.close();
    };
  }, []);

  const sendMessage = () => {
    const testMessage: ServerMessage = {
      sender: "range-control",
      message: "a really cool message",
    };

    socketRef.current?.send(JSON.stringify(testMessage));
  };

  return (
    <>
      <div className="text-xl">RANGE CONTROL</div>
      <button onClick={sendMessage}>Send Message to RPI</button>
    </>
  );
};
