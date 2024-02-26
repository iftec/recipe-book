// Import functions to test
const { makeFetchRequest, addToFavorites } = require('./script');

// Mock fetch function
global.fetch = jest.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve({ success: true }),
  })
);

describe('makeFetchRequest', () => {
  it('should make a POST request with the correct URL, method, headers, and body', async () => {
    // Mock data
    const url = 'https://example.com/api/recipes';
    const method = 'POST';
    const data = { recipeName: 'Pasta', ingredients: ['Tomatoes', 'Cheese'] };

    // Call the function
    await makeFetchRequest(url, method, data);

    // Assert fetch was called with the correct arguments
    expect(fetch).toHaveBeenCalledWith(url, {
      method: method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
  });

  it('should return the response data', async () => {
    // Mock data
    const url = 'https://example.com/api/recipes';
    const method = 'POST';
    const data = { recipeName: 'Pasta', ingredients: ['Tomatoes', 'Cheese'] };

    // Call the function
    const response = await makeFetchRequest(url, method, data);

    // Assert the response data
    expect(response).toEqual({ success: true });
  });
});

describe('addToFavorites', () => {
  it('should make a POST request to add a recipe to favorites', async () => {
    // Mock makeFetchRequest
    const makeFetchRequestMock = jest.fn();

    // Assign the mock function to window.makeFetchRequest
    window.makeFetchRequest = makeFetchRequestMock;

    // Call the function
    await addToFavorites(123);

   
  });
});
