import { useCallback, useEffect, useState } from 'react'
import './App.css'

const API = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:5000'

function App() {
  const [tasks, setTasks] = useState([])
  const [title, setTitle] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadTasks = useCallback(async () => {
    try {
      const response = await fetch(`${API}/api/tasks`)
      if (!response.ok) throw new Error('Could not load tasks')
      setTasks(await response.json())
      setError('')
    } catch {
      setError('Cannot connect to the API. Check Flask and PostgreSQL.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadTasks()
  }, [loadTasks])

  async function addTask(event) {
    event.preventDefault()
    if (!title.trim()) return

    try {
      setError('')
      const response = await fetch(`${API}/api/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: title.trim() }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.error || 'Could not add task')

      setTasks(current => [...current, data])
      setTitle('')
    } catch (err) {
      setError(err.message || 'Could not add task')
    }
  }

  async function toggleTask(task) {
    try {
      setError('')
      const response = await fetch(`${API}/api/tasks/${task.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ completed: !task.completed }),
      })
      const updated = await response.json()
      if (!response.ok) throw new Error(updated.error || 'Could not update task')

      setTasks(current =>
        current.map(item => item.id === updated.id ? updated : item)
      )
    } catch (err) {
      setError(err.message || 'Could not update task')
    }
  }

  async function deleteTask(id) {
    try {
      setError('')
      const response = await fetch(`${API}/api/tasks/${id}`, {
        method: 'DELETE',
      })
      if (!response.ok) throw new Error('Could not delete task')

      setTasks(current => current.filter(task => task.id !== id))
    } catch (err) {
      setError(err.message || 'Could not delete task')
    }
  }

  const completed = tasks.filter(task => task.completed).length

  return (
    <main className="page">
      <section className="panel">
        <header className="header">
          <div className="brand-icon">T</div>
          <div>
            <h1>TaskFlow</h1>
            <p className="subtitle">Your work, organized.</p>
          </div>
          <span className="counter">{completed}/{tasks.length} done</span>
        </header>

        <form className="task-form" onSubmit={addTask}>
          <input
            aria-label="New task title"
            placeholder="What needs to get done?"
            value={title}
            maxLength={200}
            onChange={event => setTitle(event.target.value)}
          />
          <button type="submit" disabled={!title.trim()}>Add task</button>
        </form>

        {error && (
          <div className="error" role="alert">
            {error}
            <button className="retry" onClick={loadTasks}>Retry</button>
          </div>
        )}

        {loading ? (
          <p className="empty">Loading your tasks...</p>
        ) : tasks.length === 0 ? (
          <div className="empty">
            <p className="empty-icon">✓</p>
            <h2>Ready when you are</h2>
            <p>Add your first task above to get started.</p>
          </div>
        ) : (
          <ul className="task-list">
            {tasks.map(task => (
              <li className="task" key={task.id}>
                <label className="task-label">
                  <input
                    type="checkbox"
                    checked={task.completed}
                    onChange={() => toggleTask(task)}
                  />
                  <span className={task.completed ? 'done' : ''}>
                    {task.title}
                  </span>
                </label>
                <button
                  className="delete"
                  onClick={() => deleteTask(task.id)}
                  aria-label={`Delete ${task.title}`}
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}

        <footer>
          <span>React</span>
          <span>Flask API</span>
          <span>PostgreSQL</span>
        </footer>
      </section>
    </main>
  )
}

export default App
