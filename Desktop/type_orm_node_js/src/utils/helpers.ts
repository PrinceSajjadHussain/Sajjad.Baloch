export const generateUniqueId = () => {
  // Get the current date and time
  let date = new Date();

  // Construct the unique ID by concatenating:
  // 1. The full year (e.g., '2024')
  // 2. The month (1-based, e.g., '9' for September)
  // 3. The day of the month (e.g., '6')
  // 4. The current time in milliseconds since Unix epoch (e.g., '1694005200000')
  let id =
    date.getFullYear().toString() +
    (date.getMonth() + 1).toString() +
    date.getDate().toString() +
    date.getTime().toString();

  // Return the generated unique ID
  return id;
}

export function convertToDate(dateString: any) {
  // Split the date and time parts
  const [datePart, timePart, period] = dateString.split(' ');

  // Extract day, month, and year
  const [day, month, year] = datePart.split('-');

  // Extract hours, minutes, seconds, and milliseconds
  const [hours, minutes, seconds] = timePart.split('.');
  const milliseconds = seconds.split('.')[1] || '000';

  // Convert month abbreviation to month index (0-11)
  const monthIndex = new Date(Date.parse(month + " 1, 2012")).getMonth();

  // Convert 12-hour format to 24-hour format
  let hour = parseInt(hours, 10);
  if (period === 'PM' && hour < 12) {
    hour += 12;
  }
  if (period === 'AM' && hour === 12) {
    hour = 0;
  }

  // Create and return the Date object
  return new Date(
    parseInt(`20${year}`, 10), // Adding '20' to the year to convert '24' to '2024'
    monthIndex,
    parseInt(day, 10),
    hour,
    parseInt(minutes, 10),
    parseInt(seconds, 10),
    parseInt(milliseconds.slice(0, 3), 10) // Ensure milliseconds are three digits
  );
}


export function generateTID(): string {
  // Define the minimum and maximum values for the 12-digit random number
  const min = 100000000000; // Minimum 12-digit number
  const max = 999999999999; // Maximum 12-digit number
  
  // Generate a random 12-digit number within the specified range
  const id = Math.floor(Math.random() * (max - min + 1)) + min;

  // Get the current date in YYYYMMDD format
  const now = new Date();
  const dateString = now.toISOString().split('T')[0].replace(/-/g, ''); // Format the date as 'YYYYMMDD'

  // Combine the date and the random 12-digit number to form the TID
  return `${dateString}-${id}`;
}


let currentTraceNo = 600520;

function getNextTraceNo() {
  // Convert the current trace number to a string and pad it with leading zeros to ensure it's 6 digits long
  const traceNo = String(currentTraceNo).padStart(6, '0');

  // Increment the current trace number for the next call
  currentTraceNo++;

  // Return the zero-padded trace number
  return traceNo;
}

export const formatDateToCustomString = () => {
  // Get the current date and time
  const date = new Date();

  // Extract the year, month, day, hours, minutes, and seconds
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are zero-based, so add 1
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');

  // Format and return the date and time as a string in the format YYYYMMDDHHMMSS
  return `${year}${month}${day}${hours}${minutes}${seconds}`;
}


export let clients: any;