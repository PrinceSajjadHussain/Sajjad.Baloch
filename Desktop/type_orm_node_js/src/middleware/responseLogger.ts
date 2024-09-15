import { Request, Response, NextFunction } from 'express';
import { Logger } from 'winston';

/**
 * Creates a middleware function that logs HTTP responses.
 * 
 * This middleware overrides the `res.send` method to include additional logging
 * functionality. It captures the response body and modifies it based on specific 
 * conditions, then logs the modified response body along with request details.
 * 
 * @param logger - A winston logger instance used for logging response details.
 * @returns An Express middleware function.
 */
export const responseLogger = (logger: Logger) => {
  return (req: Request, res: Response, next: NextFunction) => {
    // Preserve the original res.send method
    const originalSend = res.send;

    // Override the res.send method to include logging functionality
    res.send = function (this: Response, body: any): Response {
      if (req.headers.tid) {
        let logMessage = typeof body === 'string' ? body : JSON.stringify(body);
        const bodyJSON = typeof body === 'string' ? JSON.parse(body) : body;

        // Modify response body based on request URL and status
        if (req.originalUrl.includes("getFiles") && bodyJSON.status === "00") {
          logMessage = { ...bodyJSON, data: { ...bodyJSON.data, files: "Base64" } };
        } else if (req.originalUrl.includes("terms_conditions") && bodyJSON.status === "00") {
          logMessage = { ...bodyJSON, data: "Base64" };
        } else if (req.originalUrl.includes("key_fact_statements") && bodyJSON.status === "00") {
          logMessage = { ...bodyJSON, data: "Base64" };
        } else {
          logMessage = bodyJSON;
        }

        // Create a log entry object with response details
        const logEntry = {
          timestamp: new Date().toISOString(),
          method: req.method,
          url: req.originalUrl,
          ip: req.ip,
          userAgent: req.get('User-Agent') || '',
          tid: req.headers.tid,
          logMessage: JSON.stringify(logMessage), // Log the modified response body
          type: 'res',
          status: this.statusCode, // HTTP status code of the response
        };

        // Log the response details using the provided logger
        logger.info(logEntry);
      }

      // Call the original res.send method with the response body
      return originalSend.call(this, body);
    } as typeof res.send;

    // Pass control to the next middleware or route handler
    next();
  };
};
