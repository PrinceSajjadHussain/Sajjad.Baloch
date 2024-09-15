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
exports.getConnectionMiddleware = exports.connectDB = void 0;
const typeorm_1 = require("typeorm");
let connection;
const connectDB = (req, res, next) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        if (!connection) {
            connection = yield (0, typeorm_1.createConnection)();
            console.log("Connected to ORACLE");
        }
        else if (!connection.isConnected) {
            connection = yield connection.connect();
            console.log("Reconnected to ORACLE");
        }
        next();
    }
    catch (error) {
        console.error("Error connecting to the database:", error);
        res.status(500).json("Database connection error");
    }
});
exports.connectDB = connectDB;
const getConnectionMiddleware = (req, res, next) => {
    try {
        req.dbConnection = (0, typeorm_1.getConnection)();
        next();
    }
    catch (error) {
        console.error("Error getting the connection:", error);
        res.status(500).send("Error getting the connection");
    }
};
exports.getConnectionMiddleware = getConnectionMiddleware;
