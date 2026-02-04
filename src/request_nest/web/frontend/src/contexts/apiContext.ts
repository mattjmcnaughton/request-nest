import { createContext } from "react";
import type { BinApiClient } from "../api/client";

export const ApiContext = createContext<BinApiClient | null>(null);
