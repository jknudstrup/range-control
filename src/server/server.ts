import express from "express";
import cors from "cors";
import { z } from "zod";

const PORT = 8081;

export const ServerMessageSchema = z.object({
  sender: z.string(),
  message: z.string(),
});

const app = express();
app.use(cors());

app.use(express.json());

app.get("/", (req, res) => {
  res.send("Hello from the Range Control Server !");
});

app.post("/message", (req, res) => {
  const msg = ServerMessageSchema.safeParse(req.body);
  if (!msg.success) {
    return res.status(400).send("Invalid request");
  }
  console.log(`Received message from ${msg.data.sender}: ${msg.data.message}`);
  // Process message here
  res.sendStatus(200);
});

// app.listen(PORT, () => {
//   console.log(`Server listening at http://localhost:${PORT}`);
// });

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Server listening at http://0.0.0.0:${PORT}`);
});
