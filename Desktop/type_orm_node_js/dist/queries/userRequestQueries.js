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
exports.userAccountDetailsInProduct = exports.findUserRequestByUniqueID = exports.findUserRequestsByID = exports.findAllUserRequests = void 0;
const typeorm_1 = require("typeorm");
const LOCAL_USER_REQUEST_1 = require("../entity/LOCAL_USER_REQUEST");
const findAllUserRequests = () => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const userRepository = (0, typeorm_1.getConnection)().getRepository(LOCAL_USER_REQUEST_1.LOCAL_USER_REQUEST);
        return userRepository.find({
            where: { BACK_END_MODULE: "25" }, order: {
                CREATED_DATETIME: 'ASC'
            }
        });
    }
    catch (error) {
        console.error("Error fetching All Accounts:", error.message);
        throw new Error("Failed to fetch all Blinks accounts");
    }
});
exports.findAllUserRequests = findAllUserRequests;
const findUserRequestsByID = (ID) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const userRepository = (0, typeorm_1.getConnection)().getRepository(LOCAL_USER_REQUEST_1.LOCAL_USER_REQUEST);
        return userRepository.find({
            where: { STR_SPARE1VAL: ID, BACK_END_MODULE: '25', MODULE_STATUS: (0, typeorm_1.In)([1, 2, 3, 4, 5, 6]) }, order: {
                CREATED_DATETIME: 'ASC'
            }
        });
    }
    catch (error) {
        console.error(`Error fetching accounts by ID ${ID} :`, error.message);
        throw new Error(`Failed to fetch accounts by ID ${ID}`);
    }
});
exports.findUserRequestsByID = findUserRequestsByID;
const findUserRequestByUniqueID = (ID) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        debugger;
        const userRepository = (0, typeorm_1.getConnection)().getRepository(LOCAL_USER_REQUEST_1.LOCAL_USER_REQUEST);
        return userRepository.find({ where: { ID: ID, BACK_END_MODULE: '25' } });
    }
    catch (error) {
        console.error(`Error fetching account by ID ${ID} :`, error.message);
        throw new Error(`Failed to fetch account by ID ${ID}`);
    }
});
exports.findUserRequestByUniqueID = findUserRequestByUniqueID;
const userAccountDetailsInProduct = (ID) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const userRepository = (0, typeorm_1.getConnection)().getRepository(LOCAL_USER_REQUEST_1.LOCAL_USER_REQUEST);
        return userRepository.find({ where: { ID: ID, BACK_END_MODULE: '25' } });
    }
    catch (error) {
        console.error(`Error fetching account details by ID ${ID} :`, error.message);
        throw new Error("Error fetching account details by ID");
    }
});
exports.userAccountDetailsInProduct = userAccountDetailsInProduct;
