// 俄罗斯方块游戏实现
class TetrisGame {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.nextCanvas = document.getElementById('nextCanvas');
        this.nextCtx = this.nextCanvas.getContext('2d');
        
        this.gridWidth = 10;
        this.gridHeight = 20;
        this.blockSize = 30;
        
        // 游戏状态
        this.grid = this.createEmptyGrid();
        this.currentPiece = null;
        this.nextPiece = null;
        this.score = 0;
        this.lines = 0;
        this.level = 1;
        this.isPlaying = false;
        this.isPaused = false;
        this.gameLoop = null;
        
        // 方块定义
        this.shapes = [
            [[1, 1, 1, 1]], // I
            [[1, 1], [1, 1]], // O
            [[0, 1, 0], [1, 1, 1]], // T
            [[0, 0, 1], [1, 1, 1]], // L
            [[1, 0, 0], [1, 1, 1]], // J
            [[0, 1, 1], [1, 1, 0]], // S
            [[1, 1, 0], [0, 1, 1]]  // Z
        ];
        
        // 方块颜色
        this.colors = [
            '#00ffff', // I - 青色
            '#ffff00', // O - 黄色
            '#800080', // T - 紫色
            '#ff8000', // L - 橙色
            '#0055ffd8', // J - 蓝色
            '#84ff00ff', // S - 绿色
            '#ff4000ff'  // Z - 红色
        ];
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.newGame();
    }
    
    createEmptyGrid() {
        return Array(this.gridHeight).fill().map(() => Array(this.gridWidth).fill(0));
    }
    
    setupEventListeners() {
        // 按钮事件
        document.getElementById('startBtn').addEventListener('click', () => this.start());
        document.getElementById('pauseBtn').addEventListener('click', () => this.pause());
        document.getElementById('resetBtn').addEventListener('click', () => this.reset());
        
        // 键盘事件
        document.addEventListener('keydown', (e) => {
            if (!this.isPlaying || this.isPaused) return;
            
            switch(e.key) {
                case 'ArrowLeft':
                    this.movePiece(-1, 0);
                    break;
                case 'ArrowRight':
                    this.movePiece(1, 0);
                    break;
                case 'ArrowDown':
                    this.movePiece(0, 1);
                    this.score += 1;
                    this.updateScore();
                    break;
                case 'ArrowUp':
                    this.rotatePiece();
                    break;
                case ' ':
                    this.dropPiece();
                    break;
            }
        });
        
        // 初始化退出界面
        this.initExitScreen();
    }
    
    newGame() {
        this.grid = this.createEmptyGrid();
        this.score = 0;
        this.lines = 0;
        this.level = 1;
        this.isPlaying = false;
        this.isPaused = false;
        
        this.spawnPiece();
        this.updateDisplay();
        this.updateScore();
    }
    
    start() {
        if (this.isPlaying && !this.isPaused) return;
        
        this.isPlaying = true;
        this.isPaused = false;
        this.gameLoop = setInterval(() => this.update(), 1000 - (this.level - 1) * 100);
    }
    
    pause() {
        if (!this.isPlaying) return;
        
        this.isPaused = !this.isPaused;
        if (this.isPaused) {
            clearInterval(this.gameLoop);
        } else {
            this.gameLoop = setInterval(() => this.update(), 1000 - (this.level - 1) * 100);
        }
    }
    
    reset() {
        clearInterval(this.gameLoop);
        this.newGame();
    }
    
    update() {
        if (!this.isPlaying || this.isPaused) return;
        
        if (!this.movePiece(0, 1)) {
            this.lockPiece();
            this.clearLines();
            this.spawnPiece();
            
            if (!this.isValidMove(this.currentPiece.shape, this.currentPiece.x, this.currentPiece.y)) {
                // 游戏结束
                this.gameOver();
            }
        }
        
        this.updateDisplay();
    }
    
    initExitScreen() {
        // 创建退出按钮
        const controlsDiv = document.querySelector('.controls');
        const exitBtn = document.createElement('button');
        exitBtn.id = 'exitBtn';
        exitBtn.textContent = '退出';
        exitBtn.addEventListener('click', () => this.showExitScreen());
        
        // 添加到按钮组
        const buttonGroup = controlsDiv.querySelector('.button-group');
        buttonGroup.appendChild(exitBtn);
        
        // 创建退出确认界面
        this.exitScreen = document.createElement('div');
        this.exitScreen.id = 'exitScreen';
        this.exitScreen.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        `;
        
        const exitContent = document.createElement('div');
        exitContent.style.cssText = `
            background: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
        `;
        
        const exitTitle = document.createElement('h2');
        exitTitle.textContent = '确认退出';
        exitTitle.style.marginBottom = '20px';
        
        const exitMessage = document.createElement('p');
        exitMessage.textContent = '确定要退出游戏吗？';
        exitMessage.style.marginBottom = '30px';
        
        const exitButtons = document.createElement('div');
        exitButtons.style.display = 'flex';
        exitButtons.style.gap = '15px';
        exitButtons.style.justifyContent = 'center';
        
        const confirmBtn = document.createElement('button');
        confirmBtn.textContent = '确定';
        confirmBtn.style.cssText = `
            padding: 10px 20px;
            background: #ff0000;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        `;
        confirmBtn.addEventListener('click', () => this.exitGame());
        
        const cancelBtn = document.createElement('button');
        cancelBtn.textContent = '取消';
        cancelBtn.style.cssText = `
            padding: 10px 20px;
            background: #333;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        `;
        cancelBtn.addEventListener('click', () => this.hideExitScreen());
        
        exitButtons.appendChild(confirmBtn);
        exitButtons.appendChild(cancelBtn);
        
        exitContent.appendChild(exitTitle);
        exitContent.appendChild(exitMessage);
        exitContent.appendChild(exitButtons);
        
        this.exitScreen.appendChild(exitContent);
        document.body.appendChild(this.exitScreen);
    }
    
    showExitScreen() {
        this.exitScreen.style.display = 'flex';
        // 暂停游戏
        if (this.isPlaying && !this.isPaused) {
            this.pause();
        }
    }
    
    hideExitScreen() {
        this.exitScreen.style.display = 'none';
    }
    
    exitGame() {
        // 关闭服务器（在浏览器环境中，我们只是关闭游戏界面）
        alert('感谢您玩俄罗斯方块游戏！');
        // 如果是在本地服务器上运行，可以关闭页面
        window.close();
    }
    
    gameOver() {
        this.isPlaying = false;
        clearInterval(this.gameLoop);
        alert(`游戏结束！\n分数: ${this.score}\n行数: ${this.lines}\n等级: ${this.level}`);
    }
    
    spawnPiece() {
        if (!this.nextPiece) {
            this.nextPiece = this.createRandomPiece();
        }
        
        this.currentPiece = this.nextPiece;
        this.nextPiece = this.createRandomPiece();
        
        this.currentPiece.x = Math.floor((this.gridWidth - this.currentPiece.shape[0].length) / 2);
        this.currentPiece.y = 0;
        
        this.updateNextPiece();
    }
    
    createRandomPiece() {
        const shapeIndex = Math.floor(Math.random() * this.shapes.length);
        return {
            shape: this.shapes[shapeIndex],
            color: this.colors[shapeIndex],
            x: 0,
            y: 0
        };
    }
    
    movePiece(dx, dy) {
        this.currentPiece.x += dx;
        this.currentPiece.y += dy;
        
        if (!this.isValidMove(this.currentPiece.shape, this.currentPiece.x, this.currentPiece.y)) {
            this.currentPiece.x -= dx;
            this.currentPiece.y -= dy;
            return false;
        }
        
        return true;
    }
    
    rotatePiece() {
        const rotatedShape = this.rotateMatrix(this.currentPiece.shape);
        
        if (this.isValidMove(rotatedShape, this.currentPiece.x, this.currentPiece.y)) {
            this.currentPiece.shape = rotatedShape;
        }
    }
    
    rotateMatrix(matrix) {
        const rows = matrix.length;
        const cols = matrix[0].length;
        const rotated = Array(cols).fill().map(() => Array(rows).fill(0));
        
        for (let i = 0; i < rows; i++) {
            for (let j = 0; j < cols; j++) {
                rotated[j][rows - 1 - i] = matrix[i][j];
            }
        }
        
        return rotated;
    }
    
    isValidMove(shape, x, y) {
        for (let row = 0; row < shape.length; row++) {
            for (let col = 0; col < shape[row].length; col++) {
                if (shape[row][col]) {
                    const newX = x + col;
                    const newY = y + row;
                    
                    if (newX < 0 || newX >= this.gridWidth || newY >= this.gridHeight) {
                        return false;
                    }
                    
                    if (newY >= 0 && this.grid[newY][newX]) {
                        return false;
                    }
                }
            }
        }
        
        return true;
    }
    
    dropPiece() {
        while (this.movePiece(0, 1)) {
            this.score += 2;
        }
        this.updateScore();
    }
    
    lockPiece() {
        for (let row = 0; row < this.currentPiece.shape.length; row++) {
            for (let col = 0; col < this.currentPiece.shape[row].length; col++) {
                if (this.currentPiece.shape[row][col]) {
                    const x = this.currentPiece.x + col;
                    const y = this.currentPiece.y + row;
                    
                    if (y >= 0) {
                        this.grid[y][x] = this.currentPiece.color;
                    }
                }
            }
        }
    }
    
    clearLines() {
        let linesCleared = 0;
        
        for (let row = this.gridHeight - 1; row >= 0; row--) {
            if (this.grid[row].every(cell => cell !== 0)) {
                this.grid.splice(row, 1);
                this.grid.unshift(Array(this.gridWidth).fill(0));
                row++;
                linesCleared++;
            }
        }
        
        if (linesCleared > 0) {
            this.lines += linesCleared;
            this.score += this.calculateLineScore(linesCleared);
            this.level = Math.floor(this.lines / 10) + 1;
            this.updateScore();
        }
    }
    
    calculateLineScore(lines) {
        const scores = [0, 100, 300, 500, 800];
        return scores[lines] * this.level;
    }
    
    updateDisplay() {
        this.drawGrid();
        this.drawPiece(this.currentPiece);
    }
    
    updateNextPiece() {
        this.nextCtx.clearRect(0, 0, this.nextCanvas.width, this.nextCanvas.height);
        
        // 计算方块居中显示的偏移量
        const pieceWidth = this.nextPiece.shape[0].length;
        const pieceHeight = this.nextPiece.shape.length;
        const canvasSize = this.nextCanvas.width;
        const totalBlockSize = this.blockSize;
        
        const offsetX = Math.floor((canvasSize / totalBlockSize - pieceWidth) / 2);
        const offsetY = Math.floor((canvasSize / totalBlockSize - pieceHeight) / 2);
        
        this.drawPiece(this.nextPiece, this.nextCtx, offsetX, offsetY);
    }
    
    updateScore() {
        document.getElementById('score').textContent = this.score;
        document.getElementById('lines').textContent = this.lines;
        document.getElementById('level').textContent = this.level;
    }
    
    drawGrid() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 绘制网格线
        this.ctx.strokeStyle = '#333';
        this.ctx.lineWidth = 1;
        
        for (let i = 0; i <= this.gridWidth; i++) {
            this.ctx.beginPath();
            this.ctx.moveTo(i * this.blockSize, 0);
            this.ctx.lineTo(i * this.blockSize, this.canvas.height);
            this.ctx.stroke();
        }
        
        for (let i = 0; i <= this.gridHeight; i++) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, i * this.blockSize);
            this.ctx.lineTo(this.canvas.width, i * this.blockSize);
            this.ctx.stroke();
        }
        
        // 绘制已锁定的方块
        for (let row = 0; row < this.gridHeight; row++) {
            for (let col = 0; col < this.gridWidth; col++) {
                if (this.grid[row][col]) {
                    this.drawBlock(col, row, this.grid[row][col]);
                }
            }
        }
    }
    
    drawPiece(piece, ctx = this.ctx, offsetX = 0, offsetY = 0) {
        for (let row = 0; row < piece.shape.length; row++) {
            for (let col = 0; col < piece.shape[row].length; col++) {
                if (piece.shape[row][col]) {
                    // 对于下一个方块预览，不需要添加piece.x和piece.y的偏移
                    const x = (ctx === this.nextCtx ? col + offsetX : piece.x + col + offsetX) * this.blockSize;
                    const y = (ctx === this.nextCtx ? row + offsetY : piece.y + row + offsetY) * this.blockSize;
                    this.drawBlock(
                        col + offsetX, 
                        row + offsetY, 
                        piece.color, 
                        ctx, 
                        ctx === this.nextCtx ? 0 : piece.x * this.blockSize, 
                        ctx === this.nextCtx ? 0 : piece.y * this.blockSize
                    );
                }
            }
        }
    }
    
    drawBlock(col, row, color, ctx = this.ctx, offsetX = 0, offsetY = 0) {
        const x = (col * this.blockSize) + offsetX;
        const y = (row * this.blockSize) + offsetY;
        
        // 绘制方块
        ctx.fillStyle = color;
        ctx.fillRect(x + 1, y + 1, this.blockSize - 2, this.blockSize - 2);
        
        // 绘制高光
        ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
        ctx.fillRect(x + 1, y + 1, this.blockSize - 2, 8);
        ctx.fillRect(x + 1, y + 1, 8, this.blockSize - 2);
        
        // 绘制阴影
        ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
        ctx.fillRect(x + this.blockSize - 9, y + 1, 8, this.blockSize - 2);
        ctx.fillRect(x + 1, y + this.blockSize - 9, this.blockSize - 2, 8);
    }
}

// 游戏初始化
window.addEventListener('DOMContentLoaded', () => {
    const game = new TetrisGame();
});