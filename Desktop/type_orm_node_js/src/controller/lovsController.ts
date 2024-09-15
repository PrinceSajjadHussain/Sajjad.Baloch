import { Request, Response } from 'express';
import { getLOVs } from '../utils/lovsUtils';
import { successResponse, errorResponse } from '../utils/responseUtils';

export const getLOVsController = (req: Request, res: Response) => {
  try {
    const lovs = getLOVs();
    res.status(200).json(successResponse({ lovs: lovs }));
  } catch (error: any) {
    console.error("Error fetching LOVs:", error.message);
    res.status(500).json(errorResponse("", error.message));
  }
};
