"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const fileController_1 = require("../controller/fileController");
const router = (0, express_1.Router)();
router.post('/saveFile', fileController_1.saveFile);
router.get('/getFiles/:id', fileController_1.getFilesById);
router.post('/deleteFile', fileController_1.deleteFile);
exports.default = router;
