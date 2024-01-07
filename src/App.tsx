import { useEffect } from "react";
// import { WebSocket } from "ws";

export const App = () => {
  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8080");

    socket.addEventListener("open", function (event) {
      socket.send("Hello Server!");
    });

    socket.addEventListener("message", function (event) {
      console.log("Message from server: ", event.data);
    });

    return () => {
      socket.close();
    };
  }, []);
  return (
    <>
      <div>
        <h1>RANGE CONTROL</h1>
      </div>
    </>
  );
};
