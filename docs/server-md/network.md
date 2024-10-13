# Networks and AsyncNetworks

| Tính năng                    | V1                              | V2                              |
|------------------------------|---------------------------------|---------------------------------|
| **Loại mạng**                | Đồng bộ (`Networks`)            | Không đồng bộ (`AsyncNetworks`) |
| **Độ nhạy**                  | GUI có thể bị khóa              | GUI nhạy hơn                    |
| **Độ phức tạp**              | Quản lý mạng đơn giản           | Phức tạp hơn, yêu cầu xử lý các cuộc gọi không đồng bộ |
| **Sự phù hợp với trường hợp sử dụng** | Các trường hợp sử dụng cơ bản, độ đồng thời thấp | Độ đồng thời cao, ứng dụng thời gian thực |

---

| Feature                      | V1                              | V2                              |
|------------------------------|---------------------------------|---------------------------------|
| **Network Type**             | Synchronous (`Networks`)        | Asynchronous (`AsyncNetworks`)  |
| **Responsiveness**           | Potentially blocked GUI         | Responsive GUI                   |
| **Complexity**               | Simpler network management      | More complex, requires handling of async calls |
| **Use Case Suitability**     | Basic use cases, low concurrency| High concurrency, real-time applications |
