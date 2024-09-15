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
exports.deleteFile = exports.getFilesById = exports.saveFile = void 0;
const fileService_1 = require("../services/fileService");
const responseUtils_1 = require("../utils/responseUtils");
const userRequestQueries_1 = require("../queries/userRequestQueries");
const saveFile = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const { id, base64, fileName } = req.body;
        if (!id || !base64 || !fileName) {
            const errorMessage = "Missing required fields: id, base64, or fileName";
            console.error("Error saving file:", errorMessage);
            res.status(400).json((0, responseUtils_1.errorResponse)("", errorMessage));
        }
        else {
            const data = yield (0, userRequestQueries_1.findUserRequestByUniqueID)(id);
            if (data.length > 0) {
                const result = yield (0, fileService_1.saveFileService)(id, base64, fileName);
                res.status(200).json((0, responseUtils_1.successResponse)(result));
            }
            else {
                const errorMessage = `ID Number ${id} does not exist.`;
                console.error("Error saving file:", errorMessage);
                res.status(204).json((0, responseUtils_1.errorResponse)("", errorMessage));
            }
        }
    }
    catch (error) {
        console.error("Error saving file:", error === null || error === void 0 ? void 0 : error.message);
        res.status(500).json((0, responseUtils_1.errorResponse)("", error === null || error === void 0 ? void 0 : error.message));
    }
});
exports.saveFile = saveFile;
const getFilesById = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const { id } = req.params;
        if (id) {
            const data = yield (0, userRequestQueries_1.findUserRequestByUniqueID)(id);
            if (data.length > 0) {
                const result = yield (0, fileService_1.getFilesByIdService)(id);
                res.status(200).json((0, responseUtils_1.successResponse)(result));
            }
            else {
                const errorMessage = `ID Number ${id} does not exist.`;
                console.error("Error retrieving files:", errorMessage);
                res.status(204).json((0, responseUtils_1.errorResponse)("", errorMessage));
            }
        }
        else {
            const errorMessage = "Missing required fields: id";
            console.error("Error retrieving files:", errorMessage);
            res.status(400).json((0, responseUtils_1.errorResponse)("", errorMessage));
        }
    }
    catch (error) {
        console.error("Error retrieving files:", error.message);
        res.status(500).json((0, responseUtils_1.errorResponse)("", error.message));
    }
});
exports.getFilesById = getFilesById;
const deleteFile = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const { id, fileName } = req.body;
        if (!id || !fileName) {
            const errorMessage = "Missing required fields: id or fileName";
            console.error("Error deleting file:", errorMessage);
            res.status(400).json((0, responseUtils_1.errorResponse)("", errorMessage));
        }
        else {
            const data = yield (0, userRequestQueries_1.findUserRequestByUniqueID)(id);
            if (data.length > 0) {
                const result = yield (0, fileService_1.deleteFileService)(id, fileName);
                res.status(200).json((0, responseUtils_1.successResponse)(result));
            }
            else {
                const errorMessage = `ID Number ${id} does not exist.`;
                console.error("Error deleting file:", errorMessage);
                res.status(204).json((0, responseUtils_1.errorResponse)("", errorMessage));
            }
        }
    }
    catch (error) {
        console.error("Error deleting file:", error.message);
        res.status(500).json((0, responseUtils_1.errorResponse)("", error.message));
    }
});
exports.deleteFile = deleteFile;
