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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.updateUserRequestService = exports.getCnicFrontByIdService = exports.getAccountDetailByIdService = exports.getUserRequestsByIdService = exports.getUserRequestsService = void 0;
const userRequestQueries_1 = require("../queries/userRequestQueries");
const typeorm_1 = require("typeorm");
const LOCAL_USER_REQUEST_1 = require("../entity/LOCAL_USER_REQUEST");
const path_1 = __importDefault(require("path"));
const promises_1 = __importDefault(require("fs/promises"));
const assetsDir = path_1.default.resolve(__dirname, '../../assets');
const getUserRequestsService = () => __awaiter(void 0, void 0, void 0, function* () {
    try {
        return (0, userRequestQueries_1.findAllUserRequests)();
    }
    catch (error) {
        console.error("Error fetching All Accounts:", error.message);
        throw new Error(error.message);
    }
});
exports.getUserRequestsService = getUserRequestsService;
const getUserRequestsByIdService = (ID) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        return (0, userRequestQueries_1.findUserRequestsByID)(ID);
    }
    catch (error) {
        console.error(`Error fetching accounts by ID ${ID} :`, error.message);
        throw new Error(error.message);
    }
});
exports.getUserRequestsByIdService = getUserRequestsByIdService;
const getAccountDetailByIdService = (ID) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        return (0, userRequestQueries_1.userAccountDetailsInProduct)(ID);
    }
    catch (error) {
        console.error(`Error fetching account details by ID ${ID} :`, error.message);
        throw new Error(error.message);
    }
});
exports.getAccountDetailByIdService = getAccountDetailByIdService;
const getCnicFrontByIdService = (id) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const fileDir = path_1.default.resolve(assetsDir, id.toString());
        const files = yield promises_1.default.readdir(fileDir);
        for (const file of files) {
            const filePath = path_1.default.resolve(fileDir, file);
            const lastDotIndex = file.lastIndexOf('.');
            const baseName = file.slice(0, lastDotIndex);
            const extension = file.slice(lastDotIndex + 1);
            if (baseName === 'cnicFront') {
                const cnicFrontData = yield promises_1.default.readFile(filePath, 'base64');
                return { id, cnicFront: cnicFrontData };
            }
        }
        throw new Error('Cnic Front Image not found');
    }
    catch (error) {
        const errMsg = error.message === "Cnic Front Image not found" ? error.message : "The specified ID doesn't exist.";
        throw new Error(errMsg);
    }
});
exports.getCnicFrontByIdService = getCnicFrontByIdService;
const updateUserRequestService = (id, userRequestData) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const connection = (0, typeorm_1.getConnection)();
        const userRequestRepository = connection.getRepository(LOCAL_USER_REQUEST_1.LOCAL_USER_REQUEST);
        const partialUserRequest = new LOCAL_USER_REQUEST_1.LOCAL_USER_REQUEST();
        Object.assign(partialUserRequest, userRequestData);
        partialUserRequest.USER_REQUEST = JSON.stringify(userRequestData.USER_REQUEST);
        const temp = yield userRequestRepository.update(id, Object.assign(Object.assign({}, userRequestData), { USER_REQUEST: JSON.stringify(userRequestData.USER_REQUEST) }));
        return { ID: id };
    }
    catch (error) {
        console.error(`Error occurred while updating account details for ID ${id} :`, error.message);
        throw new Error(`Failed to update account details for ID ${id}`);
    }
});
exports.updateUserRequestService = updateUserRequestService;
