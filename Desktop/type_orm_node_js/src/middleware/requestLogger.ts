import { Request, Response, NextFunction } from 'express';
import { Logger } from 'winston';

/**
 * Creates a middleware function that logs incoming HTTP requests.
 * 
 * This middleware logs details about each request, including the HTTP method, URL,
 * IP address, user agent, transaction ID (TID), and a modified version of the request body.
 * The modified request body includes placeholder values for certain properties if they are present.
 * 
 * @param logger - A winston logger instance used for logging request details.
 * @returns An Express middleware function.
 */
export const requestLogger = (logger: Logger) => {
  return (req: Request, res: Response, next: NextFunction) => {
    // Modify the request body based on specific properties
    const body = req?.body?.hasOwnProperty("base64") ? 
      { ...req?.body, base64: "base64" } :
      req.body.hasOwnProperty("liveImage") ? 
      { ...req.body, liveImage: "base64" } :
      req.body.hasOwnProperty("accountType") ? 
      { ...req?.body, cnicFront: "base64", cnicBack: "base64" } : 
      req.body;

    // Create a log entry object with request details
    const logEntry = {
      timestamp: new Date().toISOString(),
      method: req.method,
      url: req.originalUrl,
      ip: req.ip,
      userAgent: req.get('User-Agent') || '',
      tid: req.headers.tid,
      logMessage: JSON.stringify(body), // Log the modified request body
      type: 'req',
      status: "", // Status will be set in the response logging, if needed
    };

    // Log the request details using the provided logger
    logger.info(logEntry);

    // Pass control to the next middleware or route handler
    next();
  };
};
