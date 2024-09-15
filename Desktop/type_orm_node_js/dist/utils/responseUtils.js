"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.errorResponse = exports.successResponse = void 0;
const successResponse = (data, message = "Success", code) => {
    return {
        status: code ? code : "00",
        message: message,
        data: data
    };
};
exports.successResponse = successResponse;
const errorResponse = (error, message = "Error", code) => {
    return {
        status: code ? code : "01",
        message: message,
        data: error
    };
};
exports.errorResponse = errorResponse;
