import { Router } from "express";
import { saveFile, getFilesById, deleteFile } from "../controller/fileController";

const router = Router();

router.post('/saveFile', saveFile);
router.get('/getFiles/:id', getFilesById); 
router.post('/deleteFile', deleteFile);


export default router;
