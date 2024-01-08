import express from "express";
import cors from "cors";
import { z } from "zod";

// import { Target, TargetSchema } from "./serverTypes";

const TargetSchema = z.enum(["target_1"]);

export type Target = z.infer<typeof TargetSchema>;

const PORT = 8081;

const targets: Record<Target, string> = {
  target_1: "192.168.11.169",
};

export const ServerMessageSchema = z.object({
  sender: z.string(),
  message: z.string(),
});

export const parseReadableStream = async (response: Response) => {
  if (!response.body) throw new Error("No response body found");
  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  let data = "";
  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }
    const decodedChunk = decoder.decode(value, { stream: true });
    data = data + decodedChunk;
  }
  // const parsedData = JSON.parse(data);
  const parsedData = data;
  return parsedData;
};

const messageTarget = async (target: Target, message: string) => {
  const ip = targets[target];
  const url = `http://${ip}/`;
  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
  return response;
};

const app = express();
app.use(cors());

app.use(express.json());

app.get("/", (req, res) => {
  res.send("Hello from the Range Control Server !");
});

app.post("/message", (req, res) => {
  console.log(req.body);
  const msg = ServerMessageSchema.safeParse(req.body);
  if (!msg.success) {
    return res.status(400).send("Invalid request");
  }
  console.log(`Received message from ${msg.data.sender}: ${msg.data.message}`);
  // Process message here
  res.sendStatus(200);
});

app.get("/triggers/:targetId", async (req, res) => {
  const targetId = TargetSchema.parse(req.params.targetId);
  // console.log("Target ID:");
  // console.log(targetId);
  const response = await messageTarget(targetId, "trigger");
  // console.log(response.body);
  const parsedBody = await parseReadableStream(response);
  console.log(parsedBody);

  res.sendStatus(200);
});

// app.listen(PORT, () => {
//   console.log(`Server listening at http://localhost:${PORT}`);
// });

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Server listening at http://0.0.0.0:${PORT}`);
});
