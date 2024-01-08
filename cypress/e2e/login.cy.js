describe('Game initialization', () => {
    beforeEach(() => {
        cy.reload();
        cy.visit('https://silverbullets.rocks')

    })
    it('Fill out registration form, badly', () => {

        cy.get('.btn_sign').click()
        cy.get(':nth-child(1) > .input').type('cypressTest')
        cy.get(':nth-child(2) > .input').type('cypressTest@gmail.com')
        cy.get(':nth-child(3) > .password').type('cypTest')
        cy.get(':nth-child(4) > .password').type('cypTest')
        cy.get('#signup').click()
        cy.wait(2000);
        cy.get('.alert').should('contain', 'too short')
    })

    it('Fill out registration form, well', () => {

        cy.get('.btn_sign').click()
        cy.get(':nth-child(1) > .input').type('cypressTest')
        cy.get(':nth-child(2) > .input').type('cypressTest@gmail.com')
        cy.get(':nth-child(3) > .password').type('Mi7y;5Ew826X')
        cy.get(':nth-child(4) > .password').type('Mi7y;5Ew826X')
        cy.get('#signup').click()
        cy.wait(2000);
        cy.get('.alert').should('contain', 'already in use')
    })

    it('Check user in DB', () => {
        cy.visit('https://silverbullets.rocks/api/admin')
        cy.get('#id_username').type('admin')
        cy.get('#id_password').type('admin')
        cy.get('.submit-row > input').click();
        cy.get('.model-user > th > a').click();
        cy.get(':nth-child(2) > .field-email').should('contain', 'cypressTest@gmail.com')
    })
})