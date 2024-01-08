import { useEffect } from "react";
import { ServerMessage } from "./server/serverTypes";
import { Target } from "./server/server"; //blah
const PORT = 8081;

const sender = "range-control";
const baseUrl = `http://localhost:${PORT}`;

const sendToServer = async (message: string) => {
  const serverMessage: ServerMessage = {
    sender,
    message,
  };
  const url = `${baseUrl}/message`;
  await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(serverMessage),
  });
};

const triggerTarget = async (message: Target) => {
  const serverMessage: ServerMessage = {
    sender,
    message,
  };
  const url = `${baseUrl}/triggers/${message}`;
  await fetch(url, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });
};

export const App = () => {
  useEffect(() => {
    sendToServer("hello server!!!");
  }, []);

  const sendMessage = async () => {
    const testMessage: ServerMessage = {
      sender,
      message: "a really cool message",
    };

    await sendToServer(testMessage.message);
  };

  return (
    <>
      <div className="text-xl">RANGE CONTROL</div>

      <div>
        <button onClick={sendMessage}>Send Message to RPI</button>
      </div>
      <div>
        <button
          className="bg-red-900"
          onClick={() => triggerTarget("target_1")}
        >
          Trigger target 1
        </button>
      </div>
    </>
  );
};
