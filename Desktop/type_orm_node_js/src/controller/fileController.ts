import { Request, Response } from "express";
import { saveFileService, getFilesByIdService, deleteFileService } from "../services/fileService";
import { successResponse, errorResponse } from "../utils/responseUtils";
import { findUserRequestByUniqueID } from "../queries/userRequestQueries";




export const saveFile = async (req: Request, res: Response) => {
  try {
    const { id, base64, fileName } = req.body;
    if (!id || !base64 || !fileName) {
      const errorMessage = "Missing required fields: id, base64, or fileName"
      console.error("Error saving file:", errorMessage)
      res.status(400).json(errorResponse("", errorMessage));
    } else {
      const data = await findUserRequestByUniqueID(id);
      if (data.length > 0) {
        const result = await saveFileService(id, base64, fileName);
        res.status(200).json(successResponse(result));

      } else {
        const errorMessage = `ID Number ${id} does not exist.`
        console.error("Error saving file:", errorMessage)
        res.status(204).json(errorResponse("", errorMessage));
      }

    }

  } catch (error: any) {
    console.error("Error saving file:", error?.message);
    res.status(500).json(errorResponse("", error?.message));
  }
};

export const getFilesById = async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    if (id) {
      const data = await findUserRequestByUniqueID(id);
      if (data.length > 0) {
        const result = await getFilesByIdService(id as string);
        res.status(200).json(successResponse(result));
      } else {
        const errorMessage = `ID Number ${id} does not exist.`
        console.error("Error retrieving files:", errorMessage)
        res.status(204).json(errorResponse("", errorMessage));

      }

    } else {
      const errorMessage = "Missing required fields: id"
      console.error("Error retrieving files:", errorMessage)
      res.status(400).json(errorResponse("", errorMessage));

    }
  } catch (error: any) {
    console.error("Error retrieving files:", error.message);
    res.status(500).json(errorResponse("", error.message));
  }
};

export const deleteFile = async (req: Request, res: Response) => {
  try {
    const { id, fileName } = req.body;
    if (!id || !fileName) {
      const errorMessage = "Missing required fields: id or fileName"
      console.error("Error deleting file:", errorMessage)
      res.status(400).json(errorResponse("", errorMessage));

    } else {
      const data = await findUserRequestByUniqueID(id);
      if (data.length > 0) {
        const result = await deleteFileService(id, fileName);
        res.status(200).json(successResponse(result));

      } else {
        const errorMessage = `ID Number ${id} does not exist.`
        console.error("Error deleting file:", errorMessage)
        res.status(204).json(errorResponse("", errorMessage));

      }
    }

  } catch (error: any) {
    console.error("Error deleting file:", error.message);
    res.status(500).json(errorResponse("", error.message));
  }
};
