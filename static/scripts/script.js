async function makeFetchRequest(url, method, data, successMessage, errorMessage) {
    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const responseData = await response.json();

        if (responseData.success) {
            if (successMessage) {
                showNotification(successMessage, true);
            }
            return responseData;
        } else {
            throw new Error(responseData.message || 'Request failed.');
        }
    } catch (error) {
        if (errorMessage) {
            showNotification(errorMessage, false);
        }
        return { success: false, message: 'An error occurred.' };
    }
}


function submitSearchForm() {
    document.getElementById('searchForm').submit();
}
