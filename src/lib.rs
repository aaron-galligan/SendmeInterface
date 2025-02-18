use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

#[pyfunction]
fn add_two_numbers(a: i32, b: i32) -> i32 {
    a + b
}

#[pymodule]
fn sendme_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(add_two_numbers, m)?)?;
    Ok(())
}