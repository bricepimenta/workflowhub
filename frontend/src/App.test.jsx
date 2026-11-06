import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor, within, cleanup } from '@testing-library/react';
import App from './App.jsx';

// Same fallback the app uses, so the tests still work if VITE_API_URL is set locally.
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

function jsonResponse(body, status = 200) {
  return { ok: status >= 200 && status < 300, status, json: async () => body };
}

// Replace fetch with a fake that answers from a { 'METHOD /path/': response } table,
// so the tests never need the real Django server.
function mockApi(routes) {
  const fake = vi.fn(async (url, options = {}) => {
    const key = `${options.method || 'GET'} ${String(url).replace(API, '')}`;
    if (!(key in routes)) throw new Error(`Unexpected request: ${key}`);
    return routes[key];
  });
  globalThis.fetch = fake;
  return fake;
}

function signIn(user = 'tester') {
  sessionStorage.setItem('token', 'abc123');
  sessionStorage.setItem('user', user);
}

function findCall(fake, key) {
  return fake.mock.calls.find(([url, options = {}]) => `${options.method || 'GET'} ${String(url).replace(API, '')}` === key);
}

beforeEach(() => {
  sessionStorage.clear();
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe('navbar', () => {
  it('shows the brand plus Login and Register when signed out', () => {
    mockApi({});
    render(<App />);
    const nav = within(screen.getByRole('navigation'));
    expect(nav.getByText('WorkFlowHub')).toBeTruthy();
    expect(nav.getByRole('button', { name: 'Login' })).toBeTruthy();
    expect(nav.getByRole('button', { name: 'Register' })).toBeTruthy();
    expect(nav.queryByRole('button', { name: 'Logout' })).toBeNull();
  });

  it('shows the username and Logout when signed in', async () => {
    signIn('tester');
    mockApi({ 'GET /tasks/': jsonResponse([]) });
    render(<App />);
    const nav = within(screen.getByRole('navigation'));
    expect(nav.getByText(/Signed in as tester/)).toBeTruthy();
    expect(nav.getByRole('button', { name: 'Logout' })).toBeTruthy();
    await screen.findByText('Your tasks (0)');
  });

  it('switches the form between sign in and create account', () => {
    mockApi({});
    render(<App />);
    expect(screen.getByText('Sign in')).toBeTruthy();
    fireEvent.click(within(screen.getByRole('navigation')).getByRole('button', { name: 'Register' }));
    expect(screen.getByText('Create account')).toBeTruthy();
  });
});

describe('new task form', () => {
  it('has a Status dropdown that defaults to Pending', async () => {
    signIn();
    mockApi({ 'GET /tasks/': jsonResponse([]) });
    render(<App />);
    await screen.findByText('Your tasks (0)');
    // With no tasks listed, the only dropdown on the page is the one in the form.
    const statusSelect = screen.getByRole('combobox');
    expect(statusSelect.value).toBe('pending');
    const options = Array.from(statusSelect.options).map((o) => o.value);
    expect(options).toEqual(['pending', 'in_progress', 'completed']);
  });

  it('sends status "pending" when the user does not change it', async () => {
    signIn();
    const fake = mockApi({
      'GET /tasks/': jsonResponse([]),
      'POST /tasks/': jsonResponse({ id: 1, title: 'Write report', description: '', status: 'pending' }, 201),
    });
    render(<App />);
    await screen.findByText('Your tasks (0)');

    fireEvent.change(screen.getByPlaceholderText('Task title'), { target: { value: 'Write report' } });
    fireEvent.submit(screen.getByRole('button', { name: 'Add task' }).closest('form'));

    await waitFor(() => expect(findCall(fake, 'POST /tasks/')).toBeTruthy());
    const body = JSON.parse(findCall(fake, 'POST /tasks/')[1].body);
    expect(body).toEqual({ title: 'Write report', description: '', status: 'pending' });
  });

  it('sends the chosen status and resets the dropdown to Pending afterwards', async () => {
    signIn();
    const fake = mockApi({
      'GET /tasks/': jsonResponse([]),
      'POST /tasks/': jsonResponse({ id: 2, title: 'Fix bug', description: '', status: 'in_progress' }, 201),
    });
    render(<App />);
    await screen.findByText('Your tasks (0)');

    fireEvent.change(screen.getByPlaceholderText('Task title'), { target: { value: 'Fix bug' } });
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'in_progress' } });
    fireEvent.submit(screen.getByRole('button', { name: 'Add task' }).closest('form'));

    await waitFor(() => expect(findCall(fake, 'POST /tasks/')).toBeTruthy());
    const body = JSON.parse(findCall(fake, 'POST /tasks/')[1].body);
    expect(body.status).toBe('in_progress');
    await waitFor(() => expect(screen.getByRole('combobox').value).toBe('pending'));
  });
});

describe('authentication', () => {
  it('logs in, stores the token and shows the task page', async () => {
    mockApi({
      'POST /login/': jsonResponse({ token: 'tok-1', username: 'alice' }),
      'GET /tasks/': jsonResponse([]),
    });
    render(<App />);

    fireEvent.change(screen.getByPlaceholderText('Username'), { target: { value: 'alice' } });
    fireEvent.change(screen.getByPlaceholderText('Password (8+ characters)'), { target: { value: 'Testpass123!' } });
    fireEvent.submit(screen.getByPlaceholderText('Username').closest('form'));

    await screen.findByText('Your tasks (0)');
    expect(sessionStorage.getItem('token')).toBe('tok-1');
    expect(within(screen.getByRole('navigation')).getByText(/Signed in as alice/)).toBeTruthy();
  });

  it('shows the error message when login fails', async () => {
    mockApi({ 'POST /login/': jsonResponse({ detail: 'Invalid credentials.' }, 400) });
    render(<App />);

    fireEvent.change(screen.getByPlaceholderText('Username'), { target: { value: 'alice' } });
    fireEvent.change(screen.getByPlaceholderText('Password (8+ characters)'), { target: { value: 'wrong-password' } });
    fireEvent.submit(screen.getByPlaceholderText('Username').closest('form'));

    await screen.findByText('Invalid credentials.');
    expect(sessionStorage.getItem('token')).toBeNull();
  });

  it('logs out from the navbar and clears the stored token', async () => {
    signIn();
    const fake = mockApi({
      'GET /tasks/': jsonResponse([]),
      'POST /logout/': { ok: true, status: 204 },
    });
    render(<App />);
    await screen.findByText('Your tasks (0)');

    fireEvent.click(within(screen.getByRole('navigation')).getByRole('button', { name: 'Logout' }));

    await waitFor(() => expect(sessionStorage.getItem('token')).toBeNull());
    expect(findCall(fake, 'POST /logout/')).toBeTruthy();
    expect(within(screen.getByRole('navigation')).getByRole('button', { name: 'Login' })).toBeTruthy();
  });
});

describe('task list', () => {
  it('renders tasks returned by the API', async () => {
    signIn();
    mockApi({
      'GET /tasks/': jsonResponse([
        { id: 1, title: 'Plan sprint', description: 'Goals for the week', status: 'in_progress' },
        { id: 2, title: 'Ship release', description: '', status: 'completed' },
      ]),
    });
    render(<App />);

    await screen.findByText('Plan sprint');
    expect(screen.getByText('Ship release')).toBeTruthy();
    expect(screen.getByText('Your tasks (2)')).toBeTruthy();
  });

  it('updates a task status through the API', async () => {
    signIn();
    const fake = mockApi({
      'GET /tasks/': jsonResponse([{ id: 7, title: 'Review PR', description: '', status: 'pending' }]),
      'PATCH /tasks/7/': jsonResponse({ id: 7, title: 'Review PR', description: '', status: 'completed' }),
    });
    render(<App />);
    await screen.findByText('Review PR');

    // Dropdowns on the page: [0] new-task form, [1] the task's own status.
    const selects = screen.getAllByRole('combobox');
    fireEvent.change(selects[1], { target: { value: 'completed' } });

    await waitFor(() => expect(findCall(fake, 'PATCH /tasks/7/')).toBeTruthy());
    expect(JSON.parse(findCall(fake, 'PATCH /tasks/7/')[1].body)).toEqual({ status: 'completed' });
  });
});
