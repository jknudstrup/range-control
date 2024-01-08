import { z } from "zod";
import { ServerMessageSchema } from "./server";

export type ServerMessage = z.infer<typeof ServerMessageSchema>;
