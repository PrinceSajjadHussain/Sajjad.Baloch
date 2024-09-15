"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getLOVs = void 0;
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const getLOVs = () => {
    try {
        // Construct the file path to the LOVs.json file
        const filePath = path_1.default.resolve(__dirname, '../../lovs_list/LOVs.json');
        // Read the file content as a UTF-8 string
        const fileData = fs_1.default.readFileSync(filePath, 'utf8');
        // Parse the JSON data and return it
        return JSON.parse(fileData);
    }
    catch (error) {
        // Throw an error if there is an issue with reading or parsing the file
        throw new Error("Failed to fetch LOVs");
    }
};
exports.getLOVs = getLOVs;
