const handleUpload = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const sessionId = localStorage.getItem('sessionId');
  
  if (!sessionId) {
    alert('No session found. Please refresh the page.');
    return;
  }
  
  try {
    const response = await fetch('http://localhost:8000/api/upload-resume', {
      method: 'POST',
      headers: {
        'X-Session-ID': sessionId
      },
      body: formData
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }

    const data = await response.json();
    // Handle successful upload
  } catch (error) {
    console.error('Upload failed:', error);
    alert(error.message);
  }
}; 