// Import the functions to be tested
const { makeFetchRequest, toggleMenu, addToFavorites, removeFromFavorites, showNotification, confirmDelete } = require('./script');

// Mocking fetch
global.fetch = jest.fn();

// Mock the showNotification function
jest.mock('./script', () => {
  return {
    ...jest.requireActual('./script'),
    showNotification: jest.fn(),
    makeFetchRequest: jest.fn()
  };
});

// Mock the window.alert method
global.alert = jest.fn();

describe('makeFetchRequest function', () => {
  test('should call fetch with correct arguments', async () => {
    // Mock data and response
    const url = '/some/url';
    const method = 'POST';
    const data = { foo: 'bar' };
    const successMessage = 'Success!';
    const errorMessage = 'Error!';
    const responseData = { success: true };

    // Mock fetch response
    global.fetch.mockResolvedValue({
      json: () => Promise.resolve(responseData)
    });

    // Call the function
    await makeFetchRequest(url, method, data, successMessage, errorMessage);

    // Assertions
    expect(global.fetch).toHaveBeenCalledWith(url, {
      method: method,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    expect(showNotification).toHaveBeenCalledWith(successMessage, true);
    expect(showNotification).toHaveBeenCalledWith(errorMessage, false);
    expect(showNotification).toHaveBeenCalledTimes(2);
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });
});

describe('addToFavorites function', () => {
  test('should call makeFetchRequest with correct arguments', async () => {
    // Mock data and response
    const url = '/add_to_favorites/123';
    const method = 'POST';
    const data = {};
    const successMessage = 'Recipe added to favorites!';
    const errorMessage = 'This recipe is already in your favorites!!';
    const responseData = { success: true };

    // Mock makeFetchRequest response
    global.makeFetchRequest.mockResolvedValue(responseData);

    // Call the function
    await addToFavorites(123);

    // Assertions
    expect(global.makeFetchRequest).toHaveBeenCalledWith(url, method, data, successMessage, errorMessage);
    expect(global.makeFetchRequest).toHaveBeenCalledTimes(1);
  });
});

describe('toggleMenu function', () => {
  test('should toggle the menu', () => {
    // Mock the menu element
    const menu = { style: { width: '0' } };
    document.querySelector = jest.fn().mockReturnValue(menu);

    // Your test code for toggleMenu function...
  });
});
