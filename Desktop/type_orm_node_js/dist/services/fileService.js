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
exports.deleteFileService = exports.getFilesByIdService = exports.saveFileService = void 0;
const fs_1 = require("fs");
const path_1 = __importDefault(require("path"));
const assetsDir = path_1.default.resolve(__dirname, '../../assets');
const metadataFile = path_1.default.resolve(assetsDir, 'metadata.json');
const ensureDirectoryExists = (directory) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        yield fs_1.promises.mkdir(directory, { recursive: true });
    }
    catch (error) {
        if (error.code !== 'EEXIST') {
            throw error;
        }
    }
});
const getMetadata = () => __awaiter(void 0, void 0, void 0, function* () {
    try {
        yield ensureDirectoryExists(assetsDir);
        const data = yield fs_1.promises.readFile(metadataFile, 'utf8');
        return JSON.parse(data);
    }
    catch (error) {
        if (error.code === 'ENOENT') {
            return [];
        }
        throw error;
    }
});
const saveMetadata = (metadata) => __awaiter(void 0, void 0, void 0, function* () {
    yield fs_1.promises.writeFile(metadataFile, JSON.stringify(metadata, null, 2), 'utf8');
});
const saveFileService = (id, base64, fileName) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const buffer = Buffer.from(base64, 'base64');
        const fileDir = path_1.default.resolve(assetsDir, id.toString());
        const filePath = path_1.default.resolve(fileDir, fileName);
        yield ensureDirectoryExists(fileDir);
        yield fs_1.promises.writeFile(filePath, buffer);
        const metadata = yield getMetadata();
        metadata.push({ id, fileName, filePath });
        yield saveMetadata(metadata);
        return { id, fileName };
    }
    catch (error) {
        throw new Error(`Failed to save ${fileName} under the ID ${id}`);
    }
});
exports.saveFileService = saveFileService;
const getFilesByIdService = (id) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const fileDir = path_1.default.resolve(assetsDir, id.toString());
        const files = yield fs_1.promises.readdir(fileDir);
        let tempFile = {};
        yield Promise.all(files.map((file) => __awaiter(void 0, void 0, void 0, function* () {
            const filePath = path_1.default.resolve(fileDir, file);
            const fileData = yield fs_1.promises.readFile(filePath, 'base64');
            const lastDotIndex = file.lastIndexOf('.');
            const baseName = file.slice(0, lastDotIndex);
            const extension = file.slice(lastDotIndex + 1);
            const keyName = [baseName, extension];
            tempFile = Object.assign(Object.assign({}, tempFile), { [keyName[0]]: fileData });
        })));
        return { id, files: tempFile };
    }
    catch (error) {
        throw new Error(`Images could not be retrieved for ID ${id} `);
    }
});
exports.getFilesByIdService = getFilesByIdService;
const deleteFileService = (id, fileName) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const fileDir = path_1.default.resolve(assetsDir, id.toString());
        // Read all files in the directory and find the one that matches the fileName without extension
        const files = yield fs_1.promises.readdir(fileDir);
        const fileToDelete = files.find(file => path_1.default.parse(file).name === fileName);
        if (!fileToDelete) {
            throw new Error(`Image named ${fileName} was not found under ID ${id}`);
        }
        const filePath = path_1.default.resolve(fileDir, fileToDelete);
        try {
            yield fs_1.promises.unlink(filePath);
        }
        catch (error) {
            if (error.code === 'ENOENT') {
                throw new Error(error.message);
            }
            throw error.message;
        }
        const metadata = yield getMetadata();
        const updatedMetadata = metadata.filter(file => !(file.id === id && file.fileName === fileToDelete));
        yield saveMetadata(updatedMetadata);
        return { message: `${fileToDelete} was deleted successfully from ID ${id}` };
    }
    catch (error) {
        if (error.code === 'ENOENT') {
            throw new Error(`ID ${id} could not be found`);
        }
        throw error.message;
    }
});
exports.deleteFileService = deleteFileService;
