import { z } from "zod";
import { ServerMessageSchema } from "./server";

export type ServerMessage = z.infer<typeof ServerMessageSchema>;

// export type Target = (typeof targets)[number];
