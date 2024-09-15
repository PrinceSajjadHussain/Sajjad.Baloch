import { Request, Response, NextFunction } from "express";
import { Logger } from "winston";

/**
 * Creates a middleware function that restricts HTTP methods and logs disallowed requests.
 * 
 * @param logger - A winston logger instance used for logging disallowed requests.
 * @returns An Express middleware function.
 */
export const methodFilter = (logger: Logger) => {
  return (req: Request, res: Response, next: NextFunction) => {
    // List of allowed HTTP methods
    const allowedMethods = ['GET', 'POST'];

    // Check if the request method is allowed
    if (!allowedMethods.includes(req.method)) {

      // Create a log entry for the disallowed request
      const logEntry = {
        timestamp: new Date().toISOString(),
        method: req.method,
        url: req.originalUrl,
        ip: req.ip,
        userAgent: req.get('User-Agent') || '',
        tid: req.headers.tid,
        logMessage: `Method ${req.method} not allowed`,
        status: 404,
        type: 'req',
      };

      // Log the entry using the provided logger
      logger.info(logEntry);

      // Send a 404 response with an error message
      return res.status(404).json({ error: `Method ${req.method} not allowed` });
    }

    // Pass control to the next middleware or route handler
    next();
  };
};
