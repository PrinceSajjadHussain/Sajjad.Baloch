import { Connection } from "typeorm";

declare module 'express-serve-static-core' {
  interface Request {
    dbConnection?: Connection;
  }
}
