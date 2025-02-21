import { NextResponse } from 'next/server';
import { writeFile } from 'fs/promises';
import { join } from 'path';

export async function POST(req: Request) {
  try {
    const formData = await req.formData();
    const file = formData.get('file') as File;
    
    if (!file) {
      return NextResponse.json(
        { error: 'No file uploaded' },
        { status: 400 }
      );
    }

    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);

    // Save the file temporarily
    const uploadDir = join(process.cwd(), 'uploads');
    const filePath = join(uploadDir, file.name);
    await writeFile(filePath, buffer);

    // Forward the file to your sherlog agent
    const response = await fetch('http://localhost:8000/ingest', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        filePath,
        fileName: file.name,
        fileType: file.type,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to process file');
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error uploading file:', error);
    return NextResponse.json(
      { error: 'Error uploading file' },
      { status: 500 }
    );
  }
} 