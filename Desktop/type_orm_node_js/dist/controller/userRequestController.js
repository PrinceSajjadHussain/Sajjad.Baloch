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
exports.updateUserRequest = exports.getAccountDetailById = exports.getUserRequestsById = exports.getUserRequests = void 0;
const userRequestService_1 = require("../services/userRequestService");
const responseUtils_1 = require("../utils/responseUtils");
const getUserRequests = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const users = yield (0, userRequestService_1.getUserRequestsService)();
        res.status(200).json((0, responseUtils_1.successResponse)(users));
    }
    catch (error) {
        console.error("Error fetching All Accounts:", error.message);
        res.status(500).json((0, responseUtils_1.errorResponse)(error.message));
    }
});
exports.getUserRequests = getUserRequests;
const getUserRequestsById = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    const { id } = req.params;
    try {
        const accountsList = yield (0, userRequestService_1.getUserRequestsByIdService)(id);
        if (accountsList.length > 0) {
            const filterList = accountsList.filter(item => item.STR_SPARE4VAL);
            if (filterList.length > 0) {
                res.status(200).json((0, responseUtils_1.successResponse)(filterList));
            }
            else {
                const errorMessage = `Failed to fetching accounts by ID ${id}`;
                console.error(`Error fetching accounts by ID ${id} :`, errorMessage);
                res.status(500).json((0, responseUtils_1.errorResponse)(errorMessage));
            }
        }
        else {
            const errorMessage = `ID Number ${id} does not exist.`;
            console.error(`Error fetching accounts by ID ${id} :`, errorMessage);
            res.status(500).json((0, responseUtils_1.errorResponse)(errorMessage));
        }
    }
    catch (error) {
        console.error(`Error fetching accounts by ID ${id} :`, error.message);
        res.status(500).json((0, responseUtils_1.errorResponse)(error.message));
    }
});
exports.getUserRequestsById = getUserRequestsById;
const getAccountDetailById = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    const { id } = req.body;
    try {
        const users = yield (0, userRequestService_1.getAccountDetailByIdService)(id);
        if (users.length > 0) {
            res.status(200).json((0, responseUtils_1.successResponse)(users[0]));
        }
        else {
            const errorMessage = `ID Number ${id} does not exist.`;
            console.error(`Error fetching account details by ID ${id} :`, errorMessage);
            res.status(500).json((0, responseUtils_1.errorResponse)(errorMessage));
        }
    }
    catch (error) {
        console.error(`Error fetching account details by ID ${id} :`, error.message);
        res.status(500).json((0, responseUtils_1.errorResponse)(error.message));
    }
});
exports.getAccountDetailById = getAccountDetailById;
const updateUserRequest = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    const { id } = req.params;
    try {
        if (!id) {
            console.error(`Error occurred while updating account details for ID ${id} :`, "Id is Missing");
            throw new Error("Id is Missing");
        }
        const result = yield (0, userRequestService_1.updateUserRequestService)(id, req.body);
        res.status(200).json((0, responseUtils_1.successResponse)(result));
    }
    catch (error) {
        const safeError = typeof (error === null || error === void 0 ? void 0 : error.message) === "object" ? JSON.parse((error === null || error === void 0 ? void 0 : error.message) ? error === null || error === void 0 ? void 0 : error.message : error) : error === null || error === void 0 ? void 0 : error.message;
        console.error(`Error occurred while updating account details for ID ${id} :`, safeError);
        res.status(500).json((0, responseUtils_1.errorResponse)(safeError, `Failed to update account details for ID ${id}`));
    }
});
exports.updateUserRequest = updateUserRequest;
