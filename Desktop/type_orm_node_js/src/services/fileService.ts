import { promises as fs } from 'fs';
import path from 'path';

interface FileMetadata {
  id: string;
  fileName: string;
  filePath: string;
}

const assetsDir = path.resolve(__dirname, '../../assets');
const metadataFile = path.resolve(assetsDir, 'metadata.json');

const ensureDirectoryExists = async (directory: string) => {
  try {
    await fs.mkdir(directory, { recursive: true });
  } catch (error: any) {
    if (error.code !== 'EEXIST') {
      throw error;
    }
  }
};

const getMetadata = async (): Promise<FileMetadata[]> => {
  try {
    await ensureDirectoryExists(assetsDir);
    const data = await fs.readFile(metadataFile, 'utf8');
    return JSON.parse(data);
  } catch (error: any) {
    if (error.code === 'ENOENT') {
      return [];
    }
    throw error;
  }
};

const saveMetadata = async (metadata: FileMetadata[]): Promise<void> => {
  await fs.writeFile(metadataFile, JSON.stringify(metadata, null, 2), 'utf8');
};

export const saveFileService = async (id: string, base64: string, fileName: string) => {
  try {
    const buffer = Buffer.from(base64, 'base64');
    const fileDir = path.resolve(assetsDir, id.toString());
    const filePath = path.resolve(fileDir, fileName);
    await ensureDirectoryExists(fileDir);
    await fs.writeFile(filePath, buffer);
    const metadata = await getMetadata();
    metadata.push({ id, fileName, filePath });
    await saveMetadata(metadata);
    return { id, fileName };

  } catch (error) {
    throw new Error(`Failed to save ${fileName} under the ID ${id}`)
  }
};

export const getFilesByIdService = async (id: string) => {
  try {
    const fileDir = path.resolve(assetsDir, id.toString());
    const files = await fs.readdir(fileDir);
    let tempFile = {}
    await Promise.all(files.map(async (file) => {
      const filePath = path.resolve(fileDir, file);
      const fileData = await fs.readFile(filePath, 'base64');
      const lastDotIndex = file.lastIndexOf('.');
      const baseName = file.slice(0, lastDotIndex);
      const extension = file.slice(lastDotIndex + 1);
      const keyName = [baseName, extension];
      tempFile = { ...tempFile, [keyName[0]]: fileData }
    }));

    return { id, files: tempFile };

  } catch (error) {
    throw new Error(`Images could not be retrieved for ID ${id} `)
  }
};

export const deleteFileService = async (id: string, fileName: string) => {
  try {
    const fileDir = path.resolve(assetsDir, id.toString());
    // Read all files in the directory and find the one that matches the fileName without extension
    const files = await fs.readdir(fileDir);
    const fileToDelete = files.find(file => path.parse(file).name === fileName);

    if (!fileToDelete) {
      throw new Error(`Image named ${fileName} was not found under ID ${id}`);
    }

    const filePath = path.resolve(fileDir, fileToDelete);

    try {
      await fs.unlink(filePath);
    } catch (error: any) {
      if (error.code === 'ENOENT') {
        throw new Error(error.message);
      }
      throw error.message;
    }

    const metadata = await getMetadata();
    const updatedMetadata = metadata.filter(file => !(file.id === id && file.fileName === fileToDelete));
    await saveMetadata(updatedMetadata);
    return { message: `${fileToDelete} was deleted successfully from ID ${id}` };

  } catch (error: any) {
    if (error.code === 'ENOENT') {
      throw new Error(`ID ${id} could not be found`);
    }
    throw error.message;

  }
};

