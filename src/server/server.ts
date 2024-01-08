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

app.post("/message", (req, res) => {
  const msg = ServerMessageSchema.safeParse(req.body);
  if (!msg.success) {
    return res.status(400).send("Invalid request");
  }
  console.log(`Received message from ${msg.data.sender}: ${msg.data.message}`);
  // Process message here
  res.sendStatus(200);
});

app.listen(PORT, () => {
  console.log(`Server listening at http://localhost:${PORT}`);
});
