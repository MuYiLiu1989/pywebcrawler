const ctx2 = document.getElementById('aqi').getContext('2d');

    // 設定圖表數據和配置
    const chartData2 = {
      labels: aqistch, // X 軸標籤
      datasets: [{
        label: 'AQI',
        data: aqinow, // Y 軸數值
        backgroundColor: 'rgba(75, 192, 192, 0.2)', // 長條顏色
        borderColor: 'rgba(75, 192, 192, 1)', // 長條邊框顏色
        borderWidth: 1
      }]
    };

    const chartOptions2 = {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: '台灣西部主要城市即時AQI', // 圖表標題
          font: {
            size: 30, // 標題字體大小
            family: 'Arial', // 標題字體
            weight: 'bold', // 標題字體粗細
            color: 'rgba(255, 99, 132, 1)' // 標題字體顏色
          }},
    	tooltip: {
    		callbacks: {
      			label: function(tooltipItem) {
      				
				var description = descriptions[tooltipItem.dataIndex]; // 根據 datasetIndex & dataIndex 取得描述

					return `${tooltipItem.dataset.label}: ${description}`;
				}
    		}
  		},
/*
[
  { label: "一月", dataset: { label: "2023 銷售額" }, raw: 30 },
  { label: "一月", dataset: { label: "2024 銷售額" }, raw: 40 }
]
*/    
        legend: {
          display: true, // 顯示圖例 (預設為 true)
          position: 'top', // 圖例位置 (可選：'top', 'bottom', 'left', 'right')
          labels: {
              font: {
                size: 24, // 字體大小
                  },
                color: 'blue' // 字體顏色
                
            }
        }
      },
      scales: {
        x: {
          ticks: {
            font: {
              size: 20, // X 軸字體大小
              family: 'Verdana', // X 軸字體
              color: 'rgba(54, 162, 235, 1)', // X 軸字體顏色
              weight: 'bold'
            }
          }
        },
        y: {
          ticks: {
            font: {
              size: 20, // Y 軸字體大小
              family: 'Verdana', // Y 軸字體
              color: 'rgba(54, 162, 235, 1)' // Y 軸字體顏色
            }
          }
        }
      }
    };

    // 建立圖表
    const myChart2 = new Chart(ctx2, {
      type: 'bar', // 圖表類型：長條圖
      data: chartData2,
      options: chartOptions2
    });