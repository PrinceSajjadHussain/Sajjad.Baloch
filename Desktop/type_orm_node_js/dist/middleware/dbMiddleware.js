"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.connectDB = void 0;
const typeorm_1 = require("typeorm");
const responseUtils_1 = require("../utils/responseUtils");
// import { logger } from '../logs/logger'; // Import the logger instance
let connection;
const MAX_RETRIES = 5;
let retryCount = 0;
const connectDB = (req, res, next) => __awaiter(void 0, void 0, void 0, function* () {
    var _a;
    try {
        if (!connection) {
            connection = yield (0, typeorm_1.createConnection)();
            console.log("Connected to ORACLE");
        }
        else if (!connection.isConnected) {
            connection = yield connection.connect();
            console.log("Reconnected to ORACLE");
        }
        retryCount = 0;
        next();
    }
    catch (error) {
        retryCount++;
        const requestId = ((_a = req.headers) === null || _a === void 0 ? void 0 : _a.tid) || 'unknown'; // Retrieve requestId from request body if available
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
            res.status(503).json((0, responseUtils_1.errorResponse)("", "Failed to connect to the Server. Please try again later", "99"));
        }
        else {
            console.error(`Database connection failed, retrying in 5 seconds...(Attempt ${retryCount} of ${MAX_RETRIES})`, error.message);
            setTimeout(() => (0, exports.connectDB)(req, res, next), 5000);
        }
    }
});
exports.connectDB = connectDB;
