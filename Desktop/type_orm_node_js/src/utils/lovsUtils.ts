import fs from 'fs';
import path from 'path';

export const getLOVs = () => {
  try {
    // Construct the file path to the LOVs.json file
    const filePath = path.resolve(__dirname, '../../lovs_list/LOVs.json');

    // Read the file content as a UTF-8 string
    const fileData = fs.readFileSync(filePath, 'utf8');

    // Parse the JSON data and return it
    return JSON.parse(fileData);

  } catch (error) {
    // Throw an error if there is an issue with reading or parsing the file
    throw new Error("Failed to fetch LOVs");
  }
};
