import { useEffect } from "react";
import { ServerMessage } from "./server/serverTypes";
const PORT = 8081;

const sendToServer = async (message: string) => {
  const serverMessage: ServerMessage = {
    sender: "range-control",
    message,
  };
  await fetch(`http://localhost:${PORT}/message`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(serverMessage),
  });
};

export const App = () => {
  useEffect(() => {
    sendToServer("hello server!!!");
  }, []);

  const sendMessage = async () => {
    const testMessage: ServerMessage = {
      sender: "range-control",
      message: "a really cool message",
    };

    await sendToServer(testMessage.message);
  };

  return (
    <>
      <div className="text-xl">RANGE CONTROL</div>
      <button onClick={sendMessage}>Send Message to RPI</button>
    </>
  );
};
