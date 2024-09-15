import { Request, Response, NextFunction } from 'express';
import { Logger } from 'winston';

/**
 * Creates a middleware function to log errors that occur during request processing.
 * 
 * This middleware captures and logs details about unhandled errors, including
 * the request method, URL, IP address, user agent, transaction ID (TID), and 
 * the error message. It also sends a generic 500 Internal Server Error response 
 * to the client.
 * 
 * @param logger - A winston logger instance used for logging error details.
 * @returns An Express middleware function that handles error logging.
 */
export const errorLogger = (logger: Logger) => {
  return (err: Error, req: Request, res: Response, next: NextFunction) => {
    // Create a log entry object with error details
    const logEntry = {
      timestamp: new Date().toISOString(),
      method: req.method, // HTTP method of the request
      url: req.originalUrl, // URL of the request
      ip: req.ip, // IP address of the client
      userAgent: req.get('User-Agent') || '', // User agent of the client
      tid: req.headers.tid, // Transaction ID, if available
      logMessage: err.message, // Error message
      type: 'error', // Type of log entry
      status: res.statusCode || 500, // HTTP status code of the response
    };

    // Log the error details using the provided logger
    logger.error(logEntry);

    // Respond with a 500 Internal Server Error status code
    res.status(500).json({ error: 'Internal Server Error' });
  };
};
