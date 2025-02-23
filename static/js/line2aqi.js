  // 獲取畫布上下文
const ctx = document.getElementById('lineChart').getContext('2d');

// 創建折線圖
const lineChart = new Chart(ctx, {
    type: 'line', // 圖表類型：折線圖
    data: {
        labels: labels, // X 軸標籤
        datasets: [
            {
                label: st0, // 圖例文字
                data: data0, // Y 軸數據
                borderColor: 'rgba(75, 192, 192, 1)', // 線條顏色
                backgroundColor: 'rgba(75, 192, 192, 0.2)', // 線條下方填充顏色
                tension: 0.4, // 線條彎曲程度 (0 為直線)
                spanGaps: true // 開啟這個選項以繪製缺少資料點之間的連線
            },
            {
                label: st1, // 第二條線
                data: data1,
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                tension: 0.4,
                spanGaps: true // 開啟這個選項以繪製缺少資料點之間的連線
            }
        ],
    },
    options: {
        responsive: true, // 自適應大小
        plugins: {
            legend: {
                display: true, // 顯示圖例 (預設為 true)
                position: 'top', // 圖例位置 (可選：'top', 'bottom', 'left', 'right')
                labels: {
                    font: {
                        size: 20, // 字體大小
                    },
                    color: 'blue' // 字體顏色
                }
            }
        },
        scales: {
            x: {
                title: {
                    display: true, // 顯示 X 軸標題
                    text: '時間',
                    font: {
                        size: 30 // X 軸標題字大小
                    },
                    color: 'blue' // X 軸標題顏色（可選）
                },
                ticks: {
                    font: {
                        size: 15 // 修改 X 軸字體大小
                    }
                }
            },
            y: {
                title: {
                    display: true, // 顯示 Y 軸標題
                    text: 'AQI',
                    font: {
                        size: 30 // X 軸標題字大小
                    },
                    color: 'green' // X 軸標題顏色（可選）
                },
                ticks: {
                    font: {
                        size: 30 // 修改 X 軸字體大小
                    }
                },
                beginAtZero: true // Y 軸從 0 開始
            }
        }
    }
});
