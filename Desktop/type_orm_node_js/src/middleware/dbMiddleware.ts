import { Request, Response, NextFunction } from "express";
import { createConnection, getConnection, Connection } from "typeorm";
import { errorResponse } from "../utils/responseUtils";
import { sendToElasticsearch } from "./userRequestMiddleware";
// import { logger } from '../logs/logger'; // Import the logger instance

let connection: Connection;
const MAX_RETRIES = 5;
let retryCount = 0;

export const connectDB = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    if (!connection) {
      connection = await createConnection();
      console.log("Connected to ORACLE");
    } else if (!connection.isConnected) {
      connection = await connection.connect();
      console.log("Reconnected to ORACLE");
    }
    retryCount = 0;
    next();
  } catch (error: any) {
    retryCount++;
    const requestId = req.headers?.tid || 'unknown'; // Retrieve requestId from request body if available
    const errorMessage = `Database connection failed: ${error.message}`;

    // Log the error using the custom logger
    // logger.error('Database Connection Error', {
    //   requestId,
    //   meta: {
    //     url: req.url,
    //     method: req.method,
    //     statusCode: 500,
    //     error: errorMessage,
    //   }
    // });

    if (retryCount > MAX_RETRIES) {
      console.error(`Maximum retry attempts reached. Stopping further retries`, error.message);
      res.status(503).json(errorResponse("", "Failed to connect to the Server. Please try again later", "99"));
    } else {
      console.error(`Database connection failed, retrying in 5 seconds...(Attempt ${retryCount} of ${MAX_RETRIES})`, error.message);
      setTimeout(() => connectDB(req, res, next), 5000);
    }
  }
};
