import { Request, Response, NextFunction } from "express";
import { generateTID } from "../utils/helpers";

/**
 * Middleware function to attach a unique Transaction ID (TID) to all JSON responses.
 * 
 * This middleware generates a unique Transaction ID (TID) for each incoming request and
 * attaches it to the request headers and all JSON responses. This is useful for tracking
 * and correlating requests and responses for debugging, logging, or analytics purposes.
 * 
 * The middleware:
 * 1. Generates a unique TID using the `generateTID` function.
 * 2. Attaches the TID to the request headers.
 * 3. Overrides the `res.json` method to include the TID in the JSON response body.
 * 4. Passes control to the next middleware or route handler in the stack.
 * 
 * @param req - The HTTP request object.
 * @param res - The HTTP response object.
 * @param next - The next middleware function in the stack.
 * 
 * @returns {void}
 */
export function tidMiddleware(req: Request, res: Response, next: NextFunction) {
  // Generate a unique Transaction ID for the request
  const tid = generateTID();

  // Attach the TID to the request headers (optional usage for logging or tracking)
  req.headers.tid = tid;

  // Preserve the original res.json function to override it
  const originalJson = res.json;

  // Override the res.json method to include the TID in all JSON responses
  res.json = function (body: any) {
    // Add the TID to the response body
    body.tid = tid;

    // Call the original res.json method with the modified body
    return originalJson.call(this, body);
  };

  // Pass control to the next middleware or route handler
  next();
}
