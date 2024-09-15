"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getLOVsController = void 0;
const lovsUtils_1 = require("../utils/lovsUtils");
const responseUtils_1 = require("../utils/responseUtils");
const getLOVsController = (req, res) => {
    try {
        const lovs = (0, lovsUtils_1.getLOVs)();
        res.status(200).json((0, responseUtils_1.successResponse)({ lovs: lovs }));
    }
    catch (error) {
        console.error("Error fetching LOVs:", error.message);
        res.status(500).json((0, responseUtils_1.errorResponse)("", error.message));
    }
};
exports.getLOVsController = getLOVsController;
